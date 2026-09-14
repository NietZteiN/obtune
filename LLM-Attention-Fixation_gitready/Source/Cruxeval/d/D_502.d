import std.math;
import std.typecons;
string f(string name) 
{
    import std.array;
    return name.split(' ').join('*');
}
unittest
{
    alias candidate = f;

    assert(candidate("Fred Smith") == "Fred*Smith");
}
void main(){}
