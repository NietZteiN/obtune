import std.math;
import std.typecons;
import std.array;
import std.conv;

Tuple!(string, string) f(string key, string value) 
{
    auto dict_ = [key: value];
    auto item = dict_.remove(key);
    return tuple(key, value);
}
unittest
{
    alias candidate = f;

    assert(candidate("read", "Is") == tuple("read", "Is"));
}
void main(){}
