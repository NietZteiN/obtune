import std.math;
import std.typecons;
import std.array;
import std.algorithm;
import std.string;

string f(string[] letters) 
{
    string[] a;
    foreach (i; 0 .. letters.length)
    {
        if (a.canFind(letters[i]))
        {
            return "no";
        }
        a ~= letters[i];
    }
    return "yes";
}
unittest
{
    alias candidate = f;

    assert(candidate(["b", "i", "r", "o", "s", "j", "v", "p"]) == "yes");
}
void main(){}
