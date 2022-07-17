`include "{{ mod_name }}.v"
module {{ mod_name }}_tb();
    // Cycle counter
    reg [15:0] cycle;

    // Input/output declarations
    {%- for lval_tp, grp in io_groups %}
    {%- for ar, vs in grp %}
    {{ lval_tp }} [{{ ar - 1 }}:0] {{ vs|map(attribute='name')|join(', ') }};
    {%- endfor %}
    {%- endfor %}
    task tick; begin
        {%- if has_clk %}
        #5 clk = ~clk;
        cycle = cycle + 1;
        #5 clk = ~clk;
        {%- else %}
        #5 cycle = cycle + 1;
        {%- endif %}
    end endtask
    {% for tc in tests %}
    task tc_{{ "%02d" |format(loop.index0) }}; begin
        $display("=== TC: {{ tc['name'] }} ===");
        {%- if has_clk %}
        clk = 0;
        {%- endif %}
        cycle = 0;
        {%- for cmd, arg in tc['exec'] %}
        {%- if cmd == 'set' %}
        {%- for k, v in arg.items() %}
        {{ k }} = {{ v }};
        {%- endfor %}
        {%- elif cmd == 'assert' %}
        {%- for k, v in arg.items() %}
        assert({{ k }} == {{ v }});
        {%- endfor %}
        {%- elif cmd == 'tick' %}
        repeat({{ arg }}) tick;
        {%- endif %}
        {%- endfor %}
    end endtask
    {% endfor %}
    initial begin
        $display("{{ disp_fmt }}", {{ disp_args }});
        $monitor("{{ mon_fmt }}", {{ mon_args }});
        {%- for tc in tests %}
        tc_{{ "%02d" |format(loop.index0) }};
        {%- endfor %}
    end
    {{ mod_name }} dut (
        {%- for v in inouts %}
        .{{ v.name }}({{v.name}}){% if not loop.last %},{% endif %}
        {%- endfor %}
    );
endmodule
