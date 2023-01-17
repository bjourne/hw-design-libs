library bjourne;
library ieee;
use ieee.float_pkg.all;
use ieee.numeric_std.all;

package types is
    type real_array2d_t is array(natural range<>) of real_vector;
    type arr1d_float32 is array(natural range<>) of float32;
end package;
