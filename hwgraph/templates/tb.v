`include "{{ mod_name }}.v"
module {{ mod_name }}_tb();
    // Input/output declarations
    {%- for ar, grp in gr_ins %}
    reg [{{ ar - 1 }}:0] {{ ', '.join(grp) }};
    {%- endfor %}
    {%- for ar, grp in gr_outs %}
    wire [{{ ar - 1 }}:0] {{ ', '.join(grp) }};
    {%- endfor %}

    {%- if clk_n_rstn %}
    {%- set clk, rstn = clk_n_rstn %}
    task tick; begin
        #5 {{ clk }} = ~{{ clk }};
        #5 {{ clk }} = ~{{ clk }};
    end endtask
    {%- endif %}
    initial begin
        $display("{{ header_fmts | join(' ') }}",
            {{ quoted_names|join(', ') }}
        );
        $monitor("{{ value_fmts|join(' ') }}", {{ names|join(', ') }});
        {% if clk_n_rstn %}

        {{ clk }} = 0;

        {%- for tc in tests %}
        $display("=== TC: %s ===", "{{ tc['name'] }}");
        {%- for vars, delta in tc['setup'] %}
        {%- for k, v in vars.items() %}
        {{ k }} = {{ v }};
        {%- endfor %}
        repeat  ({{ delta }}) tick;
        {%- endfor %}
        {%- for k, v in tc['post'].items() %}
        assert({{ k }} == {{ v }});
        {%- endfor %}
        {%- endfor %}

        {%- else %}
        {%- for values in assignments %}
        #5 {%- for v, (n, _) in zip(values, ins) %} {{ n }} = {{ v }}; {%- endfor %}
        {%- endfor %}
        {%- endif %}
    end
    {{ mod_name }} dut (
        {%- for n in names %}
        .{{n }}({{n}}){% if not loop.last %},{% endif %}
        {%- endfor %}
    );
endmodule
