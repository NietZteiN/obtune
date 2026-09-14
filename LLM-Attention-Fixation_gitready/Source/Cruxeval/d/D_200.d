import std.math;
import std.typecons;
string f(string text, string value) 
{
    size_t length = text.length;
    size_t index = 0;
    while (length > 0) {
        value = text[index] ~ value;
        length--;
        index++;
    }
    return value;
}
unittest
{
    alias candidate = f;

    assert(candidate("jao mt", "house") == "tm oajhouse");
}
void main(){}
