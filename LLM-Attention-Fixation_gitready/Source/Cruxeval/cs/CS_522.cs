using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<float> F(List<long> numbers) {
        List<float> floats = new List<float>();
        foreach(var n in numbers)
        {
            floats.Add(n % 1);
        }
        return floats.Contains(1) ? floats : new List<float>();
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)100L, (long)101L, (long)102L, (long)103L, (long)104L, (long)105L, (long)106L, (long)107L, (long)108L, (long)109L, (long)110L, (long)111L, (long)112L, (long)113L, (long)114L, (long)115L, (long)116L, (long)117L, (long)118L, (long)119L}))).SequenceEqual((new List<float>())));
    }

}
