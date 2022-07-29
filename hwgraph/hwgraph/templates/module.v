module {{ mod_name }} ({{ inouts|map(attribute='name')|join(', ')  }});
    {%- for lval_tp, grp in io_groups %}
    {%- for ar, vs in grp %}
    {{ lval_tp }} [{{ ar - 1 }}:0] {{ vs|map(attribute='name')|join(', ') }};
    {%- endfor %}
    {%- endfor %}
    {% if regs_per_clk %}
    // Registers
    {%- for clk, regs in regs_per_clk %}
    {%- for v in regs %}
    reg [{{ v.output[0].arity - 1 }}:0] {{ v.name }};
    {%- endfor %}
    {%- endfor %}
    {%- for clk, regs in regs_per_clk %}
    always @(posedge {{ clk }}) begin
        {%- for v in regs %}
        {%- set inp = v.predecessors[1] %}
        {%- if inp.type.name == 'if' %}
        {{ v.name }} <= {{ inp.name }};
        {%- else %}
        {{ v.name }} <= {{ render_rval(inp, None) }};
        {%- endif %}
        {%- endfor %}
    end
    {%- endfor %}
    {%- endif %}
    {%- if explicit or implicit %}
    // Internal wires
    {% for v in explicit %}
    {{ render_lval('wire', v) }} = {{ render_rval(v, None) }};
    {%- endfor %}
    {% for v in implicit %}
    {{ render_lval('wire', v) }} = {{ render_rval(v, None) }};
    {%- endfor %}
    {%- endif %}

    // Output wires
    {%- for v in outputs %}
    {{ render_lval('wire', v) }} = {{ render_rval(v, None) }};
    {%- endfor %}
endmodule
