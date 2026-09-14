import std.math;
import std.typecons;
import std.array;
import std.conv;

long f(string[] items, string item) 
{
    while (items.back == item) {
        items.popBack();
    }
    items ~= item;
    return items.length;
}
unittest
{
    alias candidate = f;

    assert(candidate(["bfreratrrbdbzagbretaredtroefcoiqrrneaosf"], "n") == 2L);
}
void main(){}
