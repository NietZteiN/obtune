import std.math;
import std.typecons;

Nullable!(long[long]) f(Nullable!(long[long]) dic) 
{
    if(dic.isNull) {
        return Nullable!(long[long]).init;
    }
    
    long[long] dic_op = dic.get();
    
    foreach(key, val; dic_op) {
        dic_op[key] = val * val;
    }
    
    return Nullable!(long[long])(dic_op);
}
unittest
{
    alias candidate = f;

{
        auto result = candidate([1L: 1L, 2L: 2L, 3L: 3L].nullable);
        assert(!result.isNull && result.get == [1L: 1L, 2L: 4L, 3L: 9L]);
}

}
void main(){}
