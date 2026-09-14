import std.math;
import std.typecons;
import std.array;
import std.string;

string f(string text, long space) 
{
    if (space < 0) {
        return text;
    }
    return text ~ std.array.replicate(" ", (text.length / 2 + space) - text.length);
}
unittest
{
    alias candidate = f;

    assert(candidate("sowpf", -7L) == "sowpf");
}
void main(){}
