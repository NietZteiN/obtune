import std.math;
import std.typecons;
import std.array;
import std.algorithm;

long[] f(Nullable!(long[long]) d) 
{
    long[] result;
    if (!d.isNull) {
        result.length = d.get.length;
        long a = 0L, b = 0L;
        while (d.get.length != 0) {
            result[a] = d.get[a];
            d.get.remove(a);
            long temp = b;
            b = (b + 1) % result.length;
            a = temp;
        }
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate(Nullable!(long[long]).init) == []);
}
void main(){}
