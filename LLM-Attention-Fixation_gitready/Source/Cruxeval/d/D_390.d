import std.math;
import std.typecons;
import std.string;

long f(string text) 
{
    if (text.strip().empty)
    {
        return text.strip().length;
    }
    return int.init;  // This is D's equivalent of returning None
}
unittest
{
    alias candidate = f;

    assert(candidate(" 	 ") == 0L);
}
void main(){}
