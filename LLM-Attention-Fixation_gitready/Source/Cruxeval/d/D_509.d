import std.math;
import std.typecons;
import std.format;

string f(long value, long width) 
{
    if (value >= 0) {
        return format("%0*d", width, value);
    } else {
        return format("-%0*d", width, -value);
    }
}
unittest
{
    alias candidate = f;

    assert(candidate(5L, 1L) == "5");
}
void main(){}
