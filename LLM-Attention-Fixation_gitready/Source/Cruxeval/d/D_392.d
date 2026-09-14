import std.math;
import std.typecons;
import std.string;
string f(string text) 
{
    if (text.toUpper == text) {
        return "ALL UPPERCASE";
    }
    return text;
}
unittest
{
    alias candidate = f;

    assert(candidate("Hello Is It MyClass") == "Hello Is It MyClass");
}
void main(){}
