import std.math;
import std.typecons;
import std.string;

long f(string file) 
{
    return file.indexOf('\n');
}
unittest
{
    alias candidate = f;

    assert(candidate("n wez szize lnson tilebi it 504n.
") == 33L);
}
void main(){}
