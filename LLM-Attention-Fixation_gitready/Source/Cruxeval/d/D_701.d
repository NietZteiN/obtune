import std.math;
import std.typecons;
import std.string;
import std.algorithm;
import std.array;

string f(string stg, string[] tabs) 
{
    foreach (tab; tabs)
    {
        stg = stg.stripRight(tab);
    }
    return stg;
}
unittest
{
    alias candidate = f;

    assert(candidate("31849 let it!31849 pass!", ["3", "1", "8", " ", "1", "9", "2", "d"]) == "31849 let it!31849 pass!");
}
void main(){}
