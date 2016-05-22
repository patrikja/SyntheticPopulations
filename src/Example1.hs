module Example1 where
import Data.List (intersperse)
import Draft

-- Example: Assume we have only two attributes, Age and Income.

data Age    = Child | Mid | Old      deriving (Eq, Ord, Show, Bounded, Enum)
data Income = Poor | Middle | Rich   deriving (Eq, Ord, Show, Bounded, Enum)

instance All Age
instance All Income

type ID     = Integer

data Agent = A {aid :: ID, aage :: Age, aincome :: Income}

fullPop :: [Agent]
fullPop = [ A 00 Child Middle
          , A 01 Child Middle
          , A 02 Mid   Middle
          , A 03 Mid   Middle
          , A 04 Child Middle
          , A 05 Mid   Middle
          , A 06 Mid   Middle
          , A 07 Child Poor
          , A 08 Child Poor
          , A 09 Child Poor
          , A 10 Mid   Poor
          , A 11 Old   Rich
          , A 12 Old   Rich
          , A 13 Child Rich
          , A 14 Child Rich
          , A 15 Mid   Rich
          ]

hista = histogram1 aage    fullPop
histb = histogram1 aincome fullPop

main = do putStrLn (showHist hista)
          putStrLn (showHist histb)
