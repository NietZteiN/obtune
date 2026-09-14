import std.math;
import std.typecons;
import std.array;

string f(string text) 
{
    auto arr = text.split();
    string[] result;
    foreach (item; arr)
    {
        if (item[$-3..$] == "day")
        {
            item ~= "y";
        }
        else
        {
            item ~= "day";
        }
        result ~= item;
    }
    return result.join(" ");
}
unittest
{
    alias candidate = f;

    assert(candidate("nwv mef ofme bdryl") == "nwvday mefday ofmeday bdrylday");
}
void main(){}
