using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> values, long item1, long item2) {
        if (values[values.Count - 1] == item2)
        {
            if (!values.Skip(1).Contains(values[0]))
            {
                values.Add(values[0]);
            }
        }
        else if (values[values.Count - 1] == item1)
        {
            if (values[0] == item2)
            {
                values.Add(values[0]);
            }
        }
        return values;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)1L})), (2L), (3L)).SequenceEqual((new List<long>(new long[]{(long)1L, (long)1L}))));
    }

}
