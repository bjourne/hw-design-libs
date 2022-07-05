module {{ mod_name }} ({{ inouts|join(', ') }});
    // Input/output declarations
    {%- for n, ar in ins %}
    {{ render_lval('input', n, ar) }};
    {%- endfor %}
    {%- for n, ar in outs %}
    {{ render_lval('output', n, ar) }};
    {%- endfor %}

    // Flip-flop assignments
    {%- for (n, ar), args in ffs %}
    reg [{{ ar - 1 }}:0] {{ n }};
    always @(posedge {{ args[0][1] }}) begin
        {{ n }} <= {{ args[1][1] }};
    end
    {%- endfor %}

    // Internal wires
    {%- for (n, tp, ar), args in internal_wires %}
    {{ render_lval('wire', n, ar) }} = {{ render_rval(tp, args) }};
    {%- endfor %}

    // Output wires
    {%- for (n, tp, ar), args in output_wires %}
    {{ render_lval('wire', n, ar) }} = {{ render_rval(tp, args) }};
    {%- endfor %}
endmodule
