{%- for name in submod_names -%}
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

    // Wires  between instances
    {%- for v, (_, new_wires) in submods %}
    {%- for n, a in new_wires %}
    wire [{{ a - 1 }}:0] {{ n }};
    {%- endfor %}
    {%- endfor %}

    // Instances
    {%- for v, (args, _) in submods %}
    {{ v.type.name }} {{ v.name }} ({{ args|join(', ') }});
    {%- endfor %}
endmodule
