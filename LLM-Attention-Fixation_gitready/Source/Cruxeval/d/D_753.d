import std.math;
import std.typecons;
import std.algorithm;
import std.array;

Nullable!(long[long]) f(Nullable!(long[long]) bag) 
{
    if (!bag.isNull) {
        auto values = bag.get().values;
        long[long] tbl;
        foreach (v; values){
            tbl[v] = values.count(v);
        }
        return Nullable!(long[long])(tbl);
    }
    return Nullable!(long[long]).init;
}
unittest
{
    alias candidate = f;

{
        auto result = candidate([0L: 0L, 1L: 0L, 2L: 0L, 3L: 0L, 4L: 0L].nullable);
        assert(!result.isNull && result.get == [0L: 5L]);
}

}
void main(){}
