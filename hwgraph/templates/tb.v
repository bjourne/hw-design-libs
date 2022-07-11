`include "{{ mod_name }}.v"
module {{ mod_name }}_tb();
    // Cycle counter for prettier printing.
    reg [15:0] cycle;

    // Input/output declarations
    {%- for ar, grp in gr_ins %}
    reg [{{ ar - 1 }}:0] {{ ', '.join(grp) }};
    {%- endfor %}
    {%- for ar, grp in gr_outs %}
    wire [{{ ar - 1 }}:0] {{ ', '.join(grp) }};
    {%- endfor %}
    {% if clk_n_rstn %}
    {%- set clk, rstn = clk_n_rstn %}
    task tick; begin
        #5 {{ clk }} = ~{{ clk }};
        cycle = cycle + 1;
        #5 {{ clk }} = ~{{ clk }};
    end endtask
    {% for tc in tests %}
    task tc_{{ "%02d" |format(loop.index0) }}; begin
        $display("=== TC: {{ tc['name'] }} ===");
        {{ clk }} = 0;
        cycle = 0;
        {%- for el in tc.get('exec', []) %}
        {% for k, v in el.get('set', {}).items() %}
        {{ k }} = {{ v }};
        {%- endfor %}
        {%- for k, v in el.get('assert', {}).items() %}
        assert({{ k }} == {{ v }});
        {%- endfor %}
        {%- if el.get('tick') %}
        repeat({{ el['tick'] }}) tick;
        {%- endif %}
        {%- endfor %}
    end endtask
    {% endfor %}
    {%- endif %}
    initial begin
        $display(
            "{{ display_fmt }}",
            {{ display_args }}
        );
        $monitor(
            "{{ monitor_fmt }}",
            {{ monitor_args }}
        );
        {% if clk_n_rstn %}
        {%- for tc in tests %}
        tc_{{ "%02d" |format(loop.index0) }};
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
