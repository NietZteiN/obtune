import std.math;
import std.typecons;
import std.array;
import std.string;

string f(string text) 
{
    auto result = appender!string();
    foreach (i, ch; text)
    {
        if (ch == toLower(ch))
            continue;
        if (text.length - 1 - i < text.lastIndexOf(toLower(ch)))
            result.put(ch);
    }
    return result.data;
}
unittest
{
    alias candidate = f;

    assert(candidate("ru") == "");
}
void main(){}
