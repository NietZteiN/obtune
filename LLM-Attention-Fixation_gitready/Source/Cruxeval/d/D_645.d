import std.math;
import std.typecons;

long f(long[] nums, long target) 
{
    long zeroCount = 0;
    long targetCount = 0;
    long targetIndex = -1;

    foreach (num; nums) {
        if (num == 0) {
            zeroCount++;
        }
        if (num == target) {
            targetCount++;
            if (targetCount == 3) {
                break;
            }
            if (targetIndex == -1) {
                targetIndex = targetIndex;
            }
        }
    }

    if (zeroCount > 0) {
        return 0;
    } else if (targetCount < 3) {
        return 1;
    } else {
        return targetIndex;
    }
}
unittest
{
    alias candidate = f;

    assert(candidate([1L, 1L, 1L, 2L], 3L) == 1L);
}
void main(){}
