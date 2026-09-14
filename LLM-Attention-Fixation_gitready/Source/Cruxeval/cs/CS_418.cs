using System;
using System.Diagnostics;
using System.Linq;

class Problem {
    public static string F(string s, string p) {
        int part_one, part_two, part_three;
        string[] arr = s.Split(new string[]{p}, StringSplitOptions.None);
        part_one = arr[0].Length;
        part_two = p.Length;
        part_three = s.Length - (arr[0].Length + p.Length);
        
        if (part_one >= 2 && part_two <= 2 && part_three >= 2) {
            char[] arr1 = arr[0].ToCharArray();
            Array.Reverse(arr1);
            char[] arr3 = arr[1].ToCharArray();
            Array.Reverse(arr3);
            return new string(arr1) + p + new string(arr3) + '#';
        }
        return arr[0] + p + arr[1];
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("qqqqq"), ("qqq")).Equals(("qqqqq")));
    }

}
