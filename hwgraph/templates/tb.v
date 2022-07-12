`include "{{ mod_name }}.v"
module {{ mod_name }}_tb();
    // Cycle counter for prettier printing.
    reg [15:0] cycle;

    // Input/output declarations
    {%- for lval_tp, grp in io_groups %}
    {%- for ar, vs in grp %}
    {{ lval_tp }} [{{ ar - 1 }}:0] {{ vs|map(attribute='name')|join(', ') }};
    {%- endfor %}
    {%- endfor %}
    {% if clk %}
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
        {% if clk %}
        {%- for tc in tests %}
        tc_{{ "%02d" |format(loop.index0) }};
        {%- endfor %}

        {%- else %}

        {%- endif %}
    end
    {{ mod_name }} dut (
        {%- for v in inouts %}
        .{{ v.name }}({{v.name}}){% if not loop.last %},{% endif %}
        {%- endfor %}
    );
endmodule
