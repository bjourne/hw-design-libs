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
        {{ v.name }} <= {{ v.predecessors[1].name }};
        {%- endfor %}
    end
    {%- endfor %}

    // Internal wires
    {%- for v in internal_wires %}
    {%- if v.type in WIRE_OWNERS %}
    {{ render_lval('wire', v) }} = {{ render_rval(v, True) }};
    {%- endif %}
    {%- endfor %}

    // Output wires
    {%- for v in output_wires %}
    {{ render_lval('wire', v) }} = {{ render_rval(v, True) }};
    {%- endfor %}
endmodule
