import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.string;

string f(string s) 
{
    int count = cast(int)s.length - 1;
    string reverse_s = s.dup.reverse().idup;;
    while (count > 0 && reverse_s[0 .. count][count/2*2 .. $].find("sea").length == 0)
    {
        count--;
        reverse_s = reverse_s[0 .. count];
    }
    return reverse_s[count .. $];
}

unittest
{
    alias candidate = f;

    assert(candidate("s a a b s d s a a s a a") == "");
}
void main(){}
