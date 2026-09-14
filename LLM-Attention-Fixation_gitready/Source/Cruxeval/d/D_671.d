import std.math;
import std.typecons;
import std.string;
import std.algorithm;

string f(string text, string char1, string char2) 
{
    string newText = text.dup;
    for (size_t i = 0; i < char1.length; ++i)
    {
        newText = replace(newText, char1[i], char2[i]);
    }
    return newText;
}
unittest
{
    alias candidate = f;

    assert(candidate("ewriyat emf rwto segya", "tey", "dgo") == "gwrioad gmf rwdo sggoa");
}
void main(){}
