import std.math;
import std.typecons;
import std.array;

string f(string string) 
{
    return string.replace("needles", "haystacks");
}
unittest
{
    alias candidate = f;

    assert(candidate("wdeejjjzsjsjjsxjjneddaddddddefsfd") == "wdeejjjzsjsjjsxjjneddaddddddefsfd");
}
void main(){}
