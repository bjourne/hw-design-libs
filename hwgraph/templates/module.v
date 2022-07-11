module {{ mod_name }} ({{ inouts|join(', ') }});
    // Input/output declarations
    {%- for ar, grp in gr_ins %}
    input [{{ ar - 1 }}:0] {{ ', '.join(grp) }};
    {%- endfor %}
    {%- for ar, grp in gr_outs %}
    output [{{ ar - 1 }}:0] {{ ', '.join(grp) }};
    {%- endfor %}

    // Flip-flop assignments
    {%- for clk, ffs in ffs_per_clk.items() %}
    {%- for n, wire, ar in ffs %}
    reg [{{ ar - 1 }}:0] {{ n }};
    {%- endfor %}
    {%- endfor %}
    {%- for clk, ffs in ffs_per_clk.items() %}
    always @(posedge {{ clk }}) begin
        {%- for n, wire, ar in ffs %}
        {{ n }} <= {{ wire }};
        {%- endfor %}
    end
    {%- endfor %}

    // Internal wires
    {%- for n, tp, ar in internal_wires %}
    {%- if tp in WIRE_OWNERS %}
    {{ render_lval('wire', tp, n, ar) }} = {{ render_rval(V, pred, n, True) }};
    {%- endif %}
    {%- endfor %}

    // Output wires
    {%- for n, tp, ar in output_wires %}
    {{ render_lval('wire', tp, n, ar) }} = {{ render_rval(V, pred, n, True) }};
    {%- endfor %}
endmodule
