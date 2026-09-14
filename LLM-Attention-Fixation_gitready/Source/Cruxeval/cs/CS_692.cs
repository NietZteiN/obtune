using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> array) {
        array.Reverse();
        for (int i = array.Count - 1; i >= 0; i--)
        {
            if (array[i] == 0)
            {
                array.RemoveAt(i);
            }
        }
        array.Reverse();
        return array;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>())).SequenceEqual((new List<long>())));
    }

}
