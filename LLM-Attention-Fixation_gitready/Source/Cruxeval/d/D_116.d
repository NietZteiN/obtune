import std.math;
import std.typecons;

Nullable!(long[long]) f(Nullable!(long[long]) d, long count) 
{
    if (!d.isNull) {
        auto dict = d.get();
        for(long i = 0; i < count; i++) {
            if (dict.length > 0) {
                dict.remove(dict.keys[0]);
            } else {
                break;
            }
        }
        return Nullable!(long[long])(dict);
    }
    return Nullable!(long[long]).init;
}
unittest
{
    alias candidate = f;

{
        auto result = candidate(Nullable!(long[long]).init, 200L);
        assert(result.isNull);
}

}
void main(){}
