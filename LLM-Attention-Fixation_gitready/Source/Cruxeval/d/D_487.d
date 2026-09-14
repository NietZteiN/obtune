import std.math;
import std.typecons;
long[] f(Nullable!(string[long]) dict) 
{
    long[] even_keys;
    if (dict.isNull) {
        return even_keys;
    }
    
    auto underlyingDict = dict.get();
    foreach (key; underlyingDict.keys) {
        if (key % 2 == 0) {
            even_keys ~= key;
        }
    }
    return even_keys;
}
unittest
{
    alias candidate = f;

    assert(candidate([4L: "a"].nullable) == [4L]);
}
void main(){}
