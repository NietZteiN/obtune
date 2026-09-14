import std.math;
import std.typecons;

Nullable!(long[string]) f(Nullable!(long[string]) dict1, Nullable!(long[string]) dict2) 
{
    if (dict1.isNull)
        return dict2;
    
    if (dict2.isNull)
        return dict1;
    
    auto result = dict1.get();
    
    foreach (key, value; dict2.get())
    {
        result[key] = value;
    }
    
    return Nullable!(long[string])(result);
}
unittest
{
    alias candidate = f;

{
        auto result = candidate(["disface": 9L, "cam": 7L].nullable, ["mforce": 5L].nullable);
        assert(!result.isNull && result.get == ["disface": 9L, "cam": 7L, "mforce": 5L]);
}

}
void main(){}
