import std.math;
import std.typecons;

Nullable!(long[long]) f(Nullable!(long[long]) array, long elem) 
{
    if (array.isNull) {
        return Nullable!(long[long]).init;
    }

    auto result = array.get;
    while (result.length != 0) {
        auto key = result.keys[result.length - 1];
        auto value = result[key];
        if (elem == key || elem == value) {
            result = array.get;
        }
        result.remove(key);
    }
    return Nullable!(long[long])(result);
}
unittest
{
    alias candidate = f;

{
        auto result = candidate(Nullable!(long[long]).init, 1L);
        assert(result.isNull);
}

}
void main(){}
