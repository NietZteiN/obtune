import std.math;
import std.typecons;
import std.ascii;

string f(string text) 
{
    auto k = 0;
    auto l = text.length - 1;
    while (!isAlpha(text[l]))
    {
        l--;
    }
    while (!isAlpha(text[k]))
    {
        k++;
    }
    if (k != 0 || l != text.length - 1)
    {
        return text[k .. l + 1];
    }
    else
    {
        return text[0 .. 1];
    }
}
unittest
{
    alias candidate = f;

    assert(candidate("timetable, 2mil") == "t");
}
void main(){}
