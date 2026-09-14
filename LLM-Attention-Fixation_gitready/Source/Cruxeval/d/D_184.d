import std.math;
import std.typecons;
import std.algorithm;
import std.range;

long[] f(long[] digits) 
{
    digits = digits.dup.reverse;
    if(digits.length < 2){
        return digits;
    }
    for(size_t i = 0; i < digits.length; i += 2){
        auto temp = digits[i];
        digits[i] = digits[i+1];
        digits[i+1] = temp;
    }
    return digits;
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 2L]) == [1L, 2L]);
}
void main(){}
