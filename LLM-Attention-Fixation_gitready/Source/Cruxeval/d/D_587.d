import std.math;
import std.typecons;
import std.algorithm;
import std.array;

Nullable!(string[long]) f(long[] nums, string fill) 
{
    if (nums.length > 0) {
        string[long] ans;
        foreach (n; nums) {
            ans[n] = fill;
        }
        return Nullable!(string[long])(ans);
    }
    return Nullable!(string[long]).init;
}
unittest
{
    alias candidate = f;

{
        auto result = candidate([0L, 1L, 1L, 2L], "abcca");
        assert(!result.isNull && result.get == [0L: "abcca", 1L: "abcca", 2L: "abcca"]);
}

}
void main(){}
