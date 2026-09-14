import std.math;
import std.typecons;
import std.string;
import std.conv;

string f(float float_number) {
    string number = to!string(float_number);
    size_t dot = number.indexOf('.');
    if (dot != -1) {
        return number[0 .. dot] ~ '.' ~ number[dot + 1 .. $].rightJustify(2, '0');
    }
    return number ~ ".00";
}

unittest
{
    alias candidate = f;

    assert(candidate(3.121) == "3.121");
}
void main(){}
