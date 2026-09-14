using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(List<string> lines) {
        for (int i = 0; i < lines.Count; i++)
        {
            lines[i] = lines[i].PadLeft((lines.Last().Length - lines[i].Length) / 2 + lines[i].Length).PadRight(lines.Last().Length);
        }
        return lines;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>(new string[]{(string)"dZwbSR", (string)"wijHeq", (string)"qluVok", (string)"dxjxbF"}))).SequenceEqual((new List<string>(new string[]{(string)"dZwbSR", (string)"wijHeq", (string)"qluVok", (string)"dxjxbF"}))));
    }

}
