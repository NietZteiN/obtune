import std.math;
import std.typecons;

long f(string query, Nullable!(long[string]) base) 
{
    if (!base.isNull) {
        long net_sum = 0;
        foreach (key, val; base.get()) {
            if (key.length == 3 && key[0] == query[0]) {
                net_sum -= val;
            }
            else if (key.length == 3 && key[2] == query[0]) {
                net_sum += val;
            }
        }
        return net_sum;
    }
    return 0;
}
unittest
{
    alias candidate = f;

    assert(candidate("a", Nullable!(long[string]).init) == 0L);
}
void main(){}
