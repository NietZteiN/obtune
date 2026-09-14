import std.math;
import std.typecons;

Nullable!(long[long]) f(Nullable!(long[long]) original, Nullable!(long[long]) string) 
{
    if(original.isNull || string.isNull) {
        return Nullable!(long[long]).init;
    }
    
    auto temp = original.get().dup;
    
    foreach(a, b; string.get()) {
        temp[b] = a;
    }
    
    return Nullable!(long[long])(temp);
}
unittest
{
    alias candidate = f;

{
        auto result = candidate([1L: -9L, 0L: -7L].nullable, [1L: 2L, 0L: 3L].nullable);
        assert(!result.isNull && result.get == [1L: -9L, 0L: -7L, 2L: 1L, 3L: 0L]);
}

}
void main(){}
