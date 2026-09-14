import std.math;
import std.typecons;
string[] f(string[] seq, string v) 
{
    string[] a;
    foreach (i; seq)
    {
        if (i.length >= v.length && i[i.length - v.length .. $] == v)
        {
            a ~= i ~ i;
        }
    }
    return a;
}
unittest
{
    alias candidate = f;

    assert(candidate(["oH", "ee", "mb", "deft", "n", "zz", "f", "abA"], "zz") == ["zzzz"]);
}
void main(){}
