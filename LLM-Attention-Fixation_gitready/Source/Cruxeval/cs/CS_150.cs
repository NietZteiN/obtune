using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> numbers, long index) {
        if (index <= 0 || index >= numbers.Count)
            return numbers;

        for (int i = (int)index; i < numbers.Count; i++)
        {
            numbers.Insert((int)index, numbers[i]);
            index += 1;
        }
        return numbers.GetRange(0, (int)index);
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)-2L, (long)4L, (long)-4L})), (0L)).SequenceEqual((new List<long>(new long[]{(long)-2L, (long)4L, (long)-4L}))));
    }

}
