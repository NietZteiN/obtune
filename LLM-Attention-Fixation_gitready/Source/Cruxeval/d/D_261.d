import std.math;
import std.typecons;
Tuple!(long[], long[]) f(long[] nums, long target) 
{
    long[] lows, higgs;
    foreach (i; nums) {
        if (i < target) {
            lows ~= i;
        } else {
            higgs ~= i;
        }
    }
    lows.length = 0;
    return tuple(lows, higgs);
}
unittest
{
    alias candidate = f;

    assert(candidate([12L, 516L, 5L, 2L, 3L, 214L, 51L], 5L) == tuple([], [12L, 516L, 5L, 214L, 51L]));
}
void main(){}
