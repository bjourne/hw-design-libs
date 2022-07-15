module {{ mod_name }} ({{ inouts|map(attribute='name')|join(', ')  }});
    // Input/output declarations
    {%- for lval_tp, grp in io_groups %}
    {%- for ar, vs in grp %}
    {{ lval_tp }} [{{ ar - 1 }}:0] {{ vs|map(attribute='name')|join(', ') }};
    {%- endfor %}
    {%- endfor %}

    // Flip-flop assignments
    {%- for clk, regs in regs_per_clk %}
    {%- for v in regs %}
    reg [{{ v.arity - 1 }}:0] {{ v.name }};
    {%- endfor %}
    {%- endfor %}
    {%- for clk, regs in regs_per_clk %}
    always @(posedge {{ clk }}) begin
        {%- for v in regs %}
        {%- set inp = v.predecessors[1] %}
        {%- if inp.type.refer_by_name %}
        {{ v.name }} <= {{ inp.name }};
        {%- else %}
        {{ v.name }} <= {{ render_rval(inp, None) }};
        {%- endif %}
        {%- endfor %}
    end
    {%- endfor %}

    // Internal wires
    {%- for v in explicitly_named %}
    {{ render_lval('wire', v) }} = {{ render_rval(v, None) }};
    {%- endfor %}
    {% for v in implicitly_named %}
    {{ render_lval('wire', v) }} = {{ render_rval(v, None) }};
    {%- endfor %}

    // Output wires
    {%- for v in outputs %}
    {{ render_lval('wire', v) }} = {{ render_rval(v, None) }};
    {%- endfor %}
endmodule
