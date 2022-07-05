`include "{{ mod_name }}.v"
module {{ mod_name }}_tb();
    {%- for n, ar in ins %}
    {{ render_lval('reg', n, ar) }};
    {%- endfor %}
    {%- for n, ar in outs %}
    {{ render_lval('wire', n, ar) }};
    {%- endfor %}

    {%- if clk_n_rstn %}
    {%- set clk = clk_n_rstn[0] %}
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
        {%- set rstn = clk_n_rstn[1] %}
        // Probably safe to clear all input variables.
        {%- for n, ar in ins %}
        {{ n }} = 0;
        {%- endfor %}
        tick;
        {{ rstn }} = 1;
        repeat (10) tick;
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
