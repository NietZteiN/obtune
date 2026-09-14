import std.math;
import std.typecons;
import std.array;
import std.string;

string f(string string) 
{
    auto l = string.dup;
    foreach_reverse(i; 0 .. l.length)
    {
        if (l[i] != ' ')
        {
            break;
        }
        l = l[0 .. i] ~ l[i+1 .. $];
    }
    return l.idup;
}
unittest
{
    alias candidate = f;

    assert(candidate("    jcmfxv     ") == "    jcmfxv");
}
void main(){}
