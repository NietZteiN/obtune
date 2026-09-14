import std.math;
import std.typecons;
Tuple!(long, long) f(Nullable!(long[string]) marks) 
{
    long highest = 0;
    long lowest = 100;
    
    foreach (value; marks.get())
    {
        if (value > highest)
            highest = value;
        if (value < lowest)
            lowest = value;
    }
    
    return tuple(highest, lowest);
}
unittest
{
    alias candidate = f;

    assert(candidate(["x": 67L, "v": 89L, "": 4L, "alij": 11L, "kgfsd": 72L, "yafby": 83L].nullable) == tuple(89L, 4L));
}
void main(){}
