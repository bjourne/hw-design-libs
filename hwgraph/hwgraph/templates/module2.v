{%- for name in submod_names %}
`include "{{ name }}.v"
{%- endfor -%}
module {{ mod_name }} (
    {{ inouts }}
);
    {%- for lval_tp, grp in io_groups %}
    {%- for ar, vs in grp %}
    {{ lval_tp }} [{{ ar - 1 }}:0] {{ vs|map(attribute='name')|join(', ') }};
    {%- endfor %}
    {%- endfor %}

    // Registers
    {%- for clk, regs in regs_per_clk %}
    {%- for v in regs %}
    reg [{{ v.output[0].arity - 1 }}:0] {{ v.name }};
    {%- endfor %}
    {%- endfor %}
    {%- for clk, regs in regs_per_clk %}
    always @(posedge {{ clk }}) begin
        {%- for v in regs %}
        {%- set inp = v.input[1][0] %}
        {%- if inp.type.name == 'if' %}
        {{ v.name }} <= {{ inp.name }};
        {%- else %}
        {{ v.name }} <= {{ render_rval(inp, None) }};
        {%- endif %}
        {%- endfor %}
    end
    {%- endfor %}

    // Named wires
    {%- for v in partitions['explicit'] %}
    {{ render_lval('wire', v) }} = {{ render_rval(v, None) }};
    {%- endfor %}

    // Wires for ifs
    {%- for v in partitions['if'] %}
    {{ render_lval('wire', v) }} = {{ render_rval(v, None) }};
    {%- endfor %}

    {%- if submods %}
    // Wires between instances
    {%- for v, (_, new_wires) in submods %}
    {%- for n, a in new_wires %}
    wire [{{ a - 1 }}:0] {{ n }};
    {%- endfor %}
    {%- endfor %}
    {%- endif %}

    {%- if submods %}
    // Instances
    {%- for v, (args, _) in submods %}
    {{ v.type.name }} {{ v.name }} ({{ args|join(', ') }});
    {%- endfor %}
    {%- endif %}

    // Output wires
    {%- for v in partitions['output'] %}
    {{ render_lval('wire', v) }} = {{ render_rval(v, None) }};
    {%- endfor %}
endmodule
