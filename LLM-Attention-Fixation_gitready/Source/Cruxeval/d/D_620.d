import std.math;
import std.typecons;
string f(string x) 
{
    string result;
    foreach (c; x)
    {
        result = c ~ " " ~ result;
    }
    return result[0 .. $ - 1];
}
unittest
{
    alias candidate = f;

    assert(candidate("lert dna ndqmxohi3") == "3 i h o x m q d n   a n d   t r e l");
}
void main(){}
